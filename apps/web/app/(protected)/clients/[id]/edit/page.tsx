import { CatalogForm } from "@/components/catalogs";
export default async function Page({params}:{params:Promise<{id:string}>}){ const {id}=await params; return <CatalogForm kind="clients" id={id}/>; }
