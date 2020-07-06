import React from 'react';
import { makeStyles, useTheme } from '@material-ui/core/styles';
import Input from '@material-ui/core/Input';
import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import Chip from '@material-ui/core/Chip';

const useStyles = makeStyles((theme) => ({
  formControl: {
    margin: theme.spacing(1),
    minWidth: 250,
    maxWidth: 500,
  },
  chips: {
    display: 'flex',
    flexWrap: 'wrap',
  },
  chip: {
    margin: 2,
  },
  noLabel: {
    marginTop: theme.spacing(3),
  },
}));

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
  PaperProps: {
    style: {
      maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
      width: 500,
    },
  },
};

function getStyles(value, comparedValue, theme) {
  return {
    fontWeight:
      comparedValue.indexOf(value) === -1
        ? theme.typography.fontWeightRegular
        : theme.typography.fontWeightMedium,
  };
}

export const FormikMultiSelectField = ({
  field,
  form,
  label,
  choices,
  ...otherProps
}): React.ReactElement => {
  const classes = useStyles();
  const theme = useTheme();
  const [selectedValues, setSelectedValues] = React.useState([]);

  const handleChange = (event) => {
    setSelectedValues(event.target.value);
    form.setFieldValue(field.name, event.target.value);
  };

  return (
    <FormControl className={classes.formControl}>
      <InputLabel id='mutiple-chip-label'>{label}</InputLabel>
      <Select
        labelId='mutiple-chip-label'
        id='mutiple-chip'
        multiple
        value={selectedValues}
        onChange={handleChange}
        input={<Input id='select-multiple-chip' />}
        renderValue={(selected: string[]) => (
          <div className={classes.chips}>
            {selected.map((value) => (
              <Chip
                key={value}
                label={choices.find((el) => el.value === value).name || ''}
                className={classes.chip}
              />
            ))}
          </div>
        )}
        MenuProps={MenuProps}
        {...otherProps}
      >
        {choices.map((choice) => (
          <MenuItem
            key={choice.value}
            value={choice.value}
            style={getStyles(choice.value, selectedValues, theme)}
          >
            {choice.name}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
};
