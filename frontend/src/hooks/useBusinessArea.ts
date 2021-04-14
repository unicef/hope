import { useParams } from 'react-router-dom';

export function useBusinessArea(): string {
  const { businessArea } = useParams();
  return businessArea;
}
