import VehicleExpenseForm from "@/components/vehicle-expense-form";

export default async function Page({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ return_to?: string }>;
}) {
  const [{ id }, query] = await Promise.all([params, searchParams]);
  const returnTo = query.return_to?.startsWith("/vehicles/")
    ? query.return_to
    : "/vehicle-expenses";
  return <VehicleExpenseForm id={id} returnTo={returnTo} />;
}
