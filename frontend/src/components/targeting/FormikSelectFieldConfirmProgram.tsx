import {
  FormControl,
  FormHelperText,
  InputLabel,
  MenuItem,
  Select,
} from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { getFullNodeFromEdgesById } from '../../utils/utils';
import { useConfirmation } from '../core/ConfirmationDialog';

export const FormikSelectFieldConfirmProgram = ({
  field,
  form,
  allProgramsEdges,
  program,
  setFieldValue,
  values,
  ...otherProps
}): React.ReactElement => {
  const { t } = useTranslation();
  const confirm = useConfirmation();

  const isInvalid = form.errors[field.name] && form.touched[field.name];

  const handleOnChange = (value, clear): void => {
    setFieldValue(field.name, value);
    if (clear) {
      setFieldValue('targetingCriteria', []);
    }
  };

  const dialogTitle = t('Programme Change');
  const dialogContent = (
    <span>
      {' '}
      {t('Are you sure you want to change the programme?')} <br />{' '}
      {t(
        'Changing the programme will result in deleting your current Targeting Criteria.',
      )}
    </span>
  );

  return (
    <FormControl variant='outlined' margin='dense' fullWidth {...otherProps}>
      <InputLabel>{otherProps.label}</InputLabel>
      <Select
        {...field}
        {...otherProps}
        name={field.name}
        value={field.value || otherProps.value}
        onChange={(e) => {
          const oldProgram = getFullNodeFromEdgesById(
            allProgramsEdges,
            field.value,
          );
          const newProgram = getFullNodeFromEdgesById(
            allProgramsEdges,
            e.target.value,
          );

          if (
            program &&
            values.targetingCriteria?.length &&
            oldProgram?.individualDataNeeded ===
              newProgram?.individualDataNeeded
          ) {
            confirm({
              title: dialogTitle,
              content: dialogContent,
            }).then(() => handleOnChange(e.target.value, true));
          } else {
            handleOnChange(e.target.value, false);
          }
        }}
        id={`textField-${field.name}`}
        error={isInvalid}
        SelectDisplayProps={{ 'data-cy': `select-${field.name}` }}
        MenuProps={{
          'data-cy': `select-options-${field.name}`,
          MenuListProps: { 'data-cy': 'select-options-container' },
        }}
      >
        {otherProps.choices.map((each) => (
          <MenuItem
            key={each.value ? each.value : each.name}
            value={each.value ? each.value : each.name}
            data-cy={`select-option-${each.name}`}
          >
            {each.labelEn || each.name || each.label}
          </MenuItem>
        ))}
      </Select>
      {isInvalid && form.errors[field.name] && (
        <FormHelperText error>{form.errors[field.name]}</FormHelperText>
      )}
    </FormControl>
  );
};
