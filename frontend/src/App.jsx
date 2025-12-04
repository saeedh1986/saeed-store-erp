import { useState } from 'react'
import { Button } from "@/components/ui/button"

function App() {
    const [count, setCount] = useState(0)

    return (
        <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-4">
            <div className="max-w-md w-full bg-white rounded-xl shadow-lg p-8 text-center space-y-6">
                <h1 className="text-3xl font-bold text-slate-900">Saeed Store ERP V2</h1>
                <p className="text-slate-500">
                    Building the foundation with ShadCN/UI + Tailwind.
                </p>

                <div className="flex justify-center gap-4">
                    <Button onClick={() => setCount((count) => count + 1)}>
                        Count is {count}
                    </Button>
                    <Button variant="outline">
                        Secondary Action
                    </Button>
                </div>

                <div className="p-4 bg-slate-100 rounded-lg text-sm text-slate-600">
                    Inventory Module Coming Soon...
                </div>
            </div>
        </div>
    )
}

export default App
