import PaymentForm from "@/components/payment-form";

export default async function Page({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ return_to?: string }>;
}) {
  const [{ id }, query] = await Promise.all([params, searchParams]);
  const returnTo = query.return_to?.startsWith("/clients/")
    ? query.return_to
    : "/payments";
  return <PaymentForm id={id} returnTo={returnTo} />;
}
