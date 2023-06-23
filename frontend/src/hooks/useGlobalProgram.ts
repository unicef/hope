import { useParams } from 'react-router-dom';

export function useGlobalProgram(): string {
  const { programId } = useParams();
  if (programId === undefined) {
    return 'all';
  }
  return programId;
}
