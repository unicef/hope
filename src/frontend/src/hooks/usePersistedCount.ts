import { useEffect, useState } from 'react';

export function usePersistedCount(
  page: number,
  countData?: { count?: number },
) {
  const [persistedCount, setPersistedCount] = useState<number | undefined>(
    undefined,
  );

  useEffect(() => {
    if (page === 0 && countData?.count !== undefined) {
      setPersistedCount(countData.count);
    }
  }, [page, countData]);

  return persistedCount;
}
