import styled from 'styled-components';
import FormControl from '@material-ui/core/FormControl';

export const StyledFormControl = styled(FormControl)`
  width: 260px;
  color: #5f6368;
  border-bottom: 0;
  .MuiOutlinedInput-root {
    border-radius: ${(props) => props.borderRadius || '4px'};
  }
`;
