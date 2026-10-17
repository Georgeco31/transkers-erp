import VehicleExpenseForm from"@/components/vehicle-expense-form";export default async function Page({searchParams}:{searchParams:Promise<{vehicle_id?:string}>}){const p=await searchParams;return <VehicleExpenseForm defaultVehicleId={p.vehicle_id}/>;}

