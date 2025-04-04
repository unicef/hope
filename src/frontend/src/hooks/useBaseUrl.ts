import { useBusinessArea } from './useBusinessArea';
import { useGlobalProgram } from './useGlobalProgram';

export function useBaseUrl(): {
  baseUrl: string;
  programId: string;
  programSlug: string;
  businessAreaSlug: string;
  businessArea: string;
  isAllPrograms: boolean;
  isGlobal: boolean;
} {
  const businessArea = useBusinessArea();
  const programId = useGlobalProgram();
  const baseUrl = `${businessArea}/programs/${programId}`;
  const isAllPrograms = programId === 'all';
  const isGlobal = businessArea === 'global';

  return {
    businessArea,
    programId,
    baseUrl,
    isAllPrograms,
    isGlobal,
    businessAreaSlug: businessArea,
    programSlug: programId,
  };
}
