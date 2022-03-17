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
