import { useParams } from 'react-router-dom';

export function useGlobalProgram(): string {
  const { program } = useParams();
  return program;
}
