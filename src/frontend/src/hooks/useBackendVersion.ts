import { useState } from 'react';


export const useBackendVersion = (): string => {

  const [version] = useState<string>('');
  // TODO: REST get backend version
  // useEffect(() => {
  //   if (data?.backendVersion) {
  //     setVersion(data.backendVersion);
  //   }
  // }, [data]);

  return version;
};
