import { useBusinessArea } from './useBusinessArea';
import { useGlobalProgram } from './useGlobalProgram';

export function useBaseUrl(): {
  baseUrl: string;
  programId: string;
  businessArea: string;
} {
  const businessArea = useBusinessArea();
  const programId = useGlobalProgram();
  const baseUrl = `${businessArea}/programs/${programId}`;
  return { businessArea, programId, baseUrl };
}
