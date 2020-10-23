import React from 'react';
import {
  FormControl,
  FormHelperText,
  MenuItem,
  InputLabel,
  Select,
} from '@material-ui/core';
import ConfirmationDialog from '../ConfirmationDialog';

export const FormikSelectFieldConfirm = ({
  field,
  form,
  withConfirm,
  confirmContent,
  confirmTitle,
  allPrograms,
  ...otherProps
}): React.ReactElement => {
  console.log(form);
  console.log('allPrograms', allPrograms);
  console.log('choices', otherProps.choices);

  // const shouldDeleteCriterias = other
  const isInvalid = form.errors[field.name] && form.touched[field.name];
  return (
    <ConfirmationDialog title={confirmTitle} content={confirmContent}>
      {(confirm) => (
        <FormControl
          variant='outlined'
          margin='dense'
          fullWidth
          {...otherProps}
        >
          <InputLabel>{otherProps.label}</InputLabel>
          <Select
            {...field}
            {...otherProps}
            name={field.name}
            value={field.value || otherProps.value}
            onChange={confirm((e) => {
              form.setFieldValue(field.name, e.target.value);
              const selectedProgram = allPrograms.find(
                (el) => el.node.id === e.target.value,
              ).node;
              if (selectedProgram.individualDataNeeded === false) {
                form.setFieldValue('candidateListCriterias', []);
              }
            })}
            id={`textField-${field.name}`}
            error={isInvalid}
            SelectDisplayProps={{ 'data-cy': `select-${field.name}` }}
            MenuProps={{
              'data-cy': `select-options-${field.name}`,
              MenuListProps: { 'data-cy': 'select-options-container' },
            }}
          >
            {otherProps.choices.map((each, index) => (
              <MenuItem
                key={each.value ? each.value : each.name}
                value={each.value ? each.value : each.name}
                data-cy={`select-option-${index}`}
              >
                {each.labelEn || each.name || each.label}
              </MenuItem>
            ))}
          </Select>
          {isInvalid && form.errors[field.name] && (
            <FormHelperText error>{form.errors[field.name]}</FormHelperText>
          )}
        </FormControl>
      )}
    </ConfirmationDialog>
  );
};
