import { useParams } from 'react-router-dom';

export function useProgram(): string {
  const { program } = useParams();
  return program;
}
