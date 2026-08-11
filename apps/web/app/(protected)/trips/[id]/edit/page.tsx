import TripForm from "@/components/trip-form"; export default async function Page({params}:{params:Promise<{id:string}>}){const{id}=await params;return <TripForm id={id}/>;}
