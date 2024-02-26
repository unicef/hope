import styled from 'styled-components';
import FormControl from '@mui/material/FormControl';

interface StyledFormControlProps {
  fullWidth?: boolean;
  borderRadius?: string;
}

export const StyledFormControl = styled(FormControl)<StyledFormControlProps>`
  width: ${(props) => (props.fullWidth ? '100%' : '260px')};
  color: #5f6368;
  border-bottom: 0;
  .MuiOutlinedInput-root {
    border-radius: ${(props) => props.borderRadius || '4px'};
  }
`;
