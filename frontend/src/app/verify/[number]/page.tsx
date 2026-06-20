import VerifyForm from "@/components/VerifyForm";

export default function VerifyNumberPage({ params }: { params: { number: string } }) {
  return <VerifyForm certNumber={params.number} />;
}
