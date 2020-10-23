import React from 'react';
import styled from 'styled-components';
import {
  Button,
  DialogContent,
  DialogTitle,
  DialogActions,
} from '@material-ui/core';
import { Dialog } from '../containers/dialogs/Dialog';

interface ConfirmationDialogProps {
  onClose?;
  onSubmit?;
  children?;
  title?;
  content?;
}
const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;

const DialogContainer = styled.div`
  width: 700px;
`;

class ConfirmationDialog extends React.Component<ConfirmationDialogProps> {
  //eslint-disable-next-line
  state = {
    open: false,
    callback: null,
  };

  show = (callback) => (event, ...restProps) => {
    if (event) {
      event.preventDefault();

      const eventToPass = {
        ...event,
        target: { ...event.target, value: event.target.value },
      };
      this.setState({
        open: true,
        callback: () => callback(eventToPass, ...restProps),
      });
    } else {
      this.setState({
        open: true,
        callback,
      });
    }
  };

  hide = () => {
    this.setState({
      open: false,
      callback: null,
    });
    if (this.props.onClose) this.props.onClose();
  };

  confirm = async () => {
    let result = null;
    if (!this.props.onSubmit) {
      result = await this.state.callback();
    } else {
      result = await this.props.onSubmit();
    }
    this.hide();
    return result;
  };

  render() {
    const { title, content } = this.props;
    return (
      <>
        {this.props.children(this.show)}
        <Dialog
          open={this.state.open}
          onClose={() => this.hide()}
          scroll='paper'
          aria-labelledby='form-dialog-title'
        >
          <DialogTitleWrapper>
            <DialogTitle id='scroll-dialog-title'>{title}</DialogTitle>
          </DialogTitleWrapper>
          <DialogContent>
            <DialogContainer>{content}</DialogContainer>
          </DialogContent>
          <DialogFooter>
            <DialogActions>
              <Button onClick={() => this.hide()}>CANCEL</Button>
              <Button
                type='submit'
                color='primary'
                variant='contained'
                onClick={() => this.confirm()}
                data-cy='button-submit'
              >
                Continue
              </Button>
            </DialogActions>
          </DialogFooter>
        </Dialog>
      </>
    );
  }
}
//eslint-disable-next-line
export default ConfirmationDialog;
