import { useParams } from 'react-router-dom';

export function useGlobalProgram(): string {
  const { programId } = useParams();
  return programId;
}
