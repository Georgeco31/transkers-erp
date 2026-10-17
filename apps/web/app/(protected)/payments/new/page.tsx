import PaymentForm from"@/components/payment-form";export default async function Page({searchParams}:{searchParams:Promise<{client_id?:string}>}){const p=await searchParams;return <PaymentForm defaultClientId={p.client_id}/>;}

