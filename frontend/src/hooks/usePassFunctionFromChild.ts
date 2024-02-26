import { useState } from 'react';

export function usePassFunctionFromChild(): [() => void, (action) => void] {
  const [childFunction, setChildFunction] = useState() as [
    () => void,
    (action) => void,
  ];
  const setChildFunctionWrapper = (action): void => {
    if (!childFunction) {
      setChildFunction(() => () => action());
    }
  };
  return [childFunction, setChildFunctionWrapper];
}
