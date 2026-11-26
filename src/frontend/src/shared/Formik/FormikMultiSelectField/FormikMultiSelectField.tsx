import { useTheme } from '@mui/material/styles';
import Input from '@mui/material/Input';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import Chip from '@mui/material/Chip';
import styled from 'styled-components';
import type { ReactElement } from 'react';
import { responsiveValue } from 'src/responsive';

const StyledFormControl = styled(FormControl)`
  margin: ${(props) => props.theme.spacing(1)};
`;

const StyledChips = styled.div`
  display: flex;
  flex-wrap: wrap;
  max-height: 150px;
  overflow-y: auto;
`;

const StyledChip = styled(Chip)`
  margin: 2px;
`;
const StyledNoLabel = styled.div`
  margin-top: ${(props) => props.theme.spacing(3)};
`;

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
  slotProps: {
    paper: {
      style: {
        maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
        width: 500,
      },
    },
  },
};

function getStyles(value, comparedValue, theme): { fontWeight: number } {
  if (!value || !comparedValue || !theme) return null;
  return {
    fontWeight:
      comparedValue.indexOf(value) === -1
        ? theme.typography.fontWeightRegular
        : theme.typography.fontWeightMedium,
  };
}

export function FormikMultiSelectField({
  field,
  form,
  label,
  choices,
  ...otherProps
}): ReactElement {
  const theme = useTheme();

  const handleChange = (event): void => {
    form.setFieldValue(field.name, event.target.value);
  };
  if (!choices) {
    return null;
  }
  return (
    <StyledFormControl
      sx={{
        minWidth: responsiveValue<number | string>(0, '500px'),
        maxWidth: responsiveValue('100%', '500px'),
        width: responsiveValue('100%', 'auto'),
      }}
    >
      {label ? (
        <InputLabel id="mutiple-chip-label">{label}</InputLabel>
      ) : (
        <StyledNoLabel />
      )}
      <Select
        labelId="mutiple-chip-label"
        id="mutiple-chip"
        multiple
        fullWidth
        data-cy={`select-${field.name}`}
        value={field.value}
        onChange={handleChange}
        input={
          <Input
            id="select-multiple-chip"
            sx={{
              width: responsiveValue('100% !important', '500px !important'),
            }}
          />
        }
        renderValue={(selected: string[]) => (
          <StyledChips>
            {selected.map((value) => (
              <StyledChip
                key={value}
                label={choices.find((el) => el.value === value)?.name || ''}
              />
            ))}
          </StyledChips>
        )}
        MenuProps={MenuProps}
        {...otherProps}
      >
        {choices.map((choice) => (
          <MenuItem
            key={choice.value}
            value={choice.value}
            style={getStyles(choice.value, field.value, theme)}
          >
            {choice.name}
          </MenuItem>
        ))}
      </Select>
    </StyledFormControl>
  );
}
