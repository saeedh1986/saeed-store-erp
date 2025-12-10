import os
import asyncio
import logging
import json
from datetime import datetime
from typing import Optional, List, Dict
from dotenv import load_dotenv
from woocommerce import API
import httpx
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Configuration
WC_URL = os.getenv("WC_URL")
WC_KEY = os.getenv("WC_KEY")
WC_SECRET = os.getenv("WC_SECRET")
ERP_API_URL = os.getenv("ERP_API_URL", "http://localhost:8000")
ERP_API_TOKEN = os.getenv("ERP_API_TOKEN", "system-admin-token")

# Logging Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Pydantic Schemas (Mirroring ERP Backend) ---
class CustomerCreate(BaseModel):
    email: str
    full_name: str
    is_active: bool = True

class OrderItemCreate(BaseModel):
    product_sku: str
    quantity: int
    unit_price: float

class OrderCreate(BaseModel):
    wc_id: int
    customer_email: str
    status: str
    total_amount: float
    currency: str
    items: List[OrderItemCreate]
    ai_risk_score: Optional[float] = None
    ai_notes: Optional[str] = None

class SyncLogCreate(BaseModel):
    entity_type: str
    entity_id: Optional[int]
    operation: str
    status: str
    details: Dict

# --- Core Logic ---

class SyncEngine:
    def __init__(self):
        self.wcapi = API(
            url=WC_URL,
            consumer_key=WC_KEY,
            consumer_secret=WC_SECRET,
            version="wc/v3"
        )
        self.erp_client = httpx.AsyncClient(
            base_url=ERP_API_URL,
            headers={"Authorization": f"Bearer {ERP_API_TOKEN}"},
            timeout=30.0
        )

    async def log_sync(self, log: SyncLogCreate):
        """Send sync log to ERP."""
        try:
            await self.erp_client.post("/api/v1/sync-logs", json=log.dict())
        except Exception as e:
            logger.error(f"Failed to send sync log: {e}")

    async def enrich_data_with_local_ai(self, order_data: Dict) -> Dict:
        """
        Antigravity Hook: Connects to local Ollama (RTX 3080).
        TODO: Connect to local Ollama (Qwen 2.5) here to analyze customer sentiment/fraud risk.
        """
        logger.info(f"Analying Order #{order_data['id']} with Local AI...")
        # Placeholder logic
        order_data['ai_risk_score'] = 0.1 # Low risk placeholder
        order_data['ai_notes'] = "Customer has good history. Address looks valid."
        return order_data

    async def get_or_create_customer(self, wc_order: Dict) -> Optional[str]:
        """Ensure customer exists in ERP."""
        email = wc_order.get('billing', {}).get('email')
        if not email:
            logger.warning("Order has no email.")
            return None

        # Check if exists
        try:
            resp = await self.erp_client.get(f"/api/v1/customers/by-email/{email}")
            if resp.status_code == 200:
                return email
        except httpx.HTTPError:
            pass # Continue to create

        # Create Customer
        customer_data = CustomerCreate(
            email=email,
            full_name=f"{wc_order['billing']['first_name']} {wc_order['billing']['last_name']}"
        )   
        
        try:
            resp = await self.erp_client.post("/api/v1/customers", json=customer_data.dict())
            if resp.status_code in [200, 201]:
                logger.info(f"Created Customer: {email}")
                return email
            else:
                logger.error(f"Failed to create customer: {resp.text}")
                return None
        except Exception as e:
            logger.error(f"Error creating customer: {e}")
            return None

    async def sync_order(self, wc_order: Dict):
        wc_id = wc_order['id']
        logger.info(f"Processing WC Order #{wc_id}")

        # 1. Idempotency Check
        try:
            resp = await self.erp_client.get(f"/api/v1/orders/by-wc-id/{wc_id}")
            if resp.status_code == 200:
                logger.info(f"Order #{wc_id} already exists. Skipping.")
                return
        except Exception as e:
            logger.error(f"Error checking order existence: {e}")
            await self.log_sync(SyncLogCreate(
                entity_type="Order", entity_id=wc_id, operation="Check", status="Fail", details={"error": str(e)}
            ))
            return

        # 2. Customer Sync
        customer_email = await self.get_or_create_customer(wc_order)
        if not customer_email:
            logger.error(f"Skipping Order #{wc_id} due to customer failure.")
            return

        # 3. AI Enrichment
        enriched_data = await self.enrich_data_with_local_ai(wc_order)

        # 4. Prepare Payload
        items = []
        for line_item in wc_order.get('line_items', []):
            items.append(OrderItemCreate(
                product_sku=line_item.get('sku', 'UNKNOWN'),
                quantity=line_item['quantity'],
                unit_price=float(line_item['price'])
            ))

        order_create = OrderCreate(
            wc_id=wc_id,
            customer_email=customer_email,
            status=wc_order['status'],
            total_amount=float(wc_order['total']),
            currency=wc_order['currency'],
            items=items,
            ai_risk_score=enriched_data.get('ai_risk_score'),
            ai_notes=enriched_data.get('ai_notes')
        )

        # 5. Send to ERP
        try:
            resp = await self.erp_client.post("/api/v1/orders", json=order_create.dict())
            if resp.status_code in [200, 201]:
                logger.info(f"Successfully synced Order #{wc_id}")
                await self.log_sync(SyncLogCreate(
                    entity_type="Order", entity_id=wc_id, operation="Create", status="Success", details={"wc_id": wc_id}
                ))
            else:
                logger.error(f"Failed to sync order: {resp.text}")
                await self.log_sync(SyncLogCreate(
                    entity_type="Order", entity_id=wc_id, operation="Create", status="Fail", details={"error": resp.text}
                ))
        except Exception as e:
            logger.error(f"Exception syncing order: {e}")
            await self.log_sync(SyncLogCreate(
                entity_type="Order", entity_id=wc_id, operation="Create", status="Fail", details={"error": str(e)}
            ))

    async def run(self):
        logger.info("Starting Sync Engine...")
        try:
            # Fetch Processing Orders
            orders = self.wcapi.get("orders", params={"status": "processing", "per_page": 10}).json()
            logger.info(f"Found {len(orders)} processing orders.")
            
            for order in orders:
                await self.sync_order(order)
                
        except Exception as e:
            logger.critical(f"Sync Engine Crash: {e}")
        finally:
            await self.erp_client.aclose()

if __name__ == "__main__":
    if not WC_URL or not WC_KEY:
        logger.error("Missing WooCommerce credentials. Please set WC_URL, WC_KEY, WC_SECRET.")
        exit(1)
        
    engine = SyncEngine()
    asyncio.run(engine.run())
