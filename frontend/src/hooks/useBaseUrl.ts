import { useBusinessArea } from './useBusinessArea';
import { useGlobalProgram } from './useGlobalProgram';

export function useBaseUrl(): {
  baseUrl: string;
  programId: string;
  businessArea: string;
  isAllPrograms: boolean;
} {
  const businessArea = useBusinessArea();
  const programId = useGlobalProgram();
  const baseUrl = `${businessArea}/programs/${programId}`;
  const isAllPrograms = programId === 'all';
  return { businessArea, programId, baseUrl, isAllPrograms };
}
