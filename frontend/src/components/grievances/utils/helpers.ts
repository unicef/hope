export const handleSelected = (
  item,
  arrayName,
  arrayOfValues,
  setFieldValue,
): void => {
  const newSelected = [...arrayOfValues];
  const selectedIndex = newSelected.indexOf(item);
  if (selectedIndex !== -1) {
    newSelected.splice(selectedIndex, 1);
  } else {
    newSelected.push(item);
  }
  setFieldValue(arrayName, newSelected);
};

export const removeItemById = (array, id: string, arrayHelpers): void => {
  const index = array?.findIndex((item) => item.id === id);
  if (index !== -1) {
    arrayHelpers.remove(index);
  }
};

export const getIndexForId = (array, id?: string): number => {
  if (!id) {
    return -1;
  }

  const index = array.findIndex((item) => item.id === id);
  return index !== -1 ? index : 0;
};
