/* eslint-disable @typescript-eslint/no-explicit-any */
import { useEffect, useState } from 'react';
import get from 'lodash/get';
import isFunction from 'lodash/isFunction';

/**
 *
 * @param array
 * @param keyExtractor
 * @param valueExtractor - if valueName = "*" whole object is used
 */
export function useArrayToDict<T>(
  array: T[] | undefined | null,
  keyExtractor: ((item: T) => string) | string,
  valueExtractor: ((item: T) => string) | string,
): { [id: string]: any } | { [id: number]: any } {
  const reduceCallback = (
    previousValue,
    currentValue,
  ): { [id: string]: any } | { [id: number]: any } => {
    let key;
    let value;
    if (isFunction(keyExtractor)) {
      // @ts-ignore
      key = keyExtractor(currentValue);
    } else {
      key = get(currentValue, keyExtractor);
    }
    if (isFunction(valueExtractor)) {
      // @ts-ignore
      value = valueExtractor(currentValue);
    } else {
      value =
        valueExtractor === '*'
          ? currentValue
          : get(currentValue, valueExtractor);
    }
    // eslint-disable-next-line no-param-reassign
    previousValue[key] = value;
    return previousValue;
  };
  const safeArray = Array.isArray(array) ? array : [];
  const [dict, setDict] = useState(() => safeArray.reduce(reduceCallback, {}));
  useEffect(() => {
    setDict(safeArray.reduce(reduceCallback, {}));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [safeArray]);
  return dict;
}
