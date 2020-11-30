import { useState, useEffect } from 'react';
import get from 'lodash/get';
import isFunction from 'lodash/isFunction';

/**
 *
 * @param array
 * @param keyName
 * @param valueName - if valueName = "*" whole object is used
 */
export function useArrayToDict<T>(
  array: T[],
  keyExtractor: ((item: T) => string)|string,
  valueExtractor: ((item: T) => string)|string,
) {
  const reduceCallback = (previousValue, currentValue) => {
    let key;
    let value;
    if (isFunction(keyExtractor)) {
      // eslint-disable-next-line @typescript-eslint/ban-ts-ignore
      // @ts-ignore
      key = keyExtractor(currentValue);
    } else {
      key = get(currentValue, keyExtractor);
    }
    if (isFunction(valueExtractor)) {
      // eslint-disable-next-line @typescript-eslint/ban-ts-ignore
      // @ts-ignore
      value = valueExtractor(currentValue);
    } else {
      value =valueExtractor === '*' ? currentValue : get(currentValue, valueExtractor);
    }
    // eslint-disable-next-line no-param-reassign
    previousValue[key] = value;
    return previousValue;
  };
  const [dict, setDict] = useState(() => array?.reduce(reduceCallback, {}));
  useEffect(() => {
    if (array) {
      setDict(array.reduce(reduceCallback, {}));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [array]);
  return dict;
}
