import { useEffect } from 'react';

export function Admin2SyncEffect({
  selectedHousehold,
  admin2,
  setFieldValue,
}: {
  selectedHousehold: any;
  admin2: any;
  setFieldValue: (field: string, value: any) => void;
}) {
  useEffect(() => {
    if (selectedHousehold?.admin2 && admin2 !== selectedHousehold.admin2) {
      setFieldValue('admin2', selectedHousehold.admin2);
    }
  }, [selectedHousehold?.admin2, admin2, setFieldValue]);
  return null;
}
