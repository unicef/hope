import { useState, useEffect } from 'react';
import { useLocation, useHistory } from 'react-router-dom';
import get from 'lodash/get';

/**
 *
 * @param array
 * @param keyName
 * @param valueName - if valueName = "*" whole object is used
 */
export function useArrayToDict(array, keyExtractor, valueExtractor) {
  const reduceCallback = (previousValue, currentValue) => {
    const key = get(currentValue, keyExtractor);
    const value =
      valueExtractor === '*' ? currentValue : get(currentValue, valueExtractor);
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
