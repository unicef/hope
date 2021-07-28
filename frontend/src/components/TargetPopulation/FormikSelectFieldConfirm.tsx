import React, { useState } from 'react';
import {
  FormControl,
  FormHelperText,
  MenuItem,
  InputLabel,
  Select,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
} from '@material-ui/core';
import { DialogFooter, DialogTitleWrapper } from '../ConfirmationDialog';
import { Dialog } from '../../containers/dialogs/Dialog';
import { getFullNodeFromEdgesById } from '../../utils/utils';
import { useTranslation } from 'react-i18next';

export const FormikSelectFieldConfirm = ({
  field,
  form,
  allProgramsEdges,
  ...otherProps
}): React.ReactElement => {
  const { t } = useTranslation();
  const [selectedProgram, setSelectedProgram] = useState(null);

  const isInvalid = form.errors[field.name] && form.touched[field.name];

  //eslint-disable-next-line
  const handleOnChange = (value, clear) => {
    form.setFieldValue(field.name, value);
    if (clear) {
      form.setFieldValue('candidateListCriterias', []);
      form.setFieldValue('criterias', []);
    }
    setSelectedProgram(null);
  };

  return (
    <>
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
              oldProgram?.individualDataNeeded ===
              newProgram?.individualDataNeeded
            ) {
              handleOnChange(e.target.value, false);
            } else {
              setSelectedProgram(e.target.value);
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
      <Dialog
        fullWidth
        minWidth='md'
        open={selectedProgram}
        onClose={() => setSelectedProgram(null)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
      >
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>
            <span>{t('Programme Change')}</span>
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          {' '}
          <span>
            {t('Are you sure you want to change the programme ?')} <br />{' '}
            {t(
              'Changing the programme will result in deleting your current Targeting Criteria.',
            )}
          </span>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setSelectedProgram(null)}>
              {t('CANCEL')}
            </Button>
            <Button
              type='submit'
              color='primary'
              variant='contained'
              onClick={() => handleOnChange(selectedProgram, true)}
              data-cy='button-submit'
            >
              {t('Continue')}
            </Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
};
