import React from 'react';
import styled from 'styled-components';
import {
  Button,
  DialogActions,
  DialogContent,
  DialogTitle,
  Typography,
} from '@material-ui/core';
import { Dialog } from '../containers/dialogs/Dialog';

interface ConfirmationDialogProps {
  onClose?;
  onSubmit?;
  children?;
  title?;
  content?;
  continueText?;
  extraContent?;
}
export const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

export const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;

export class ConfirmationDialog extends React.Component<ConfirmationDialogProps> {
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

  hide = (): void => {
    const { onClose } = this.props;
    this.setState({
      open: false,
      callback: null,
    });
    if (onClose) onClose();
  };

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  confirm = async (): Promise<any> => {
    let result;
    const { onSubmit } = this.props;
    const { callback } = this.state;
    if (!onSubmit) {
      result = await callback();
    } else {
      result = await onSubmit();
    }
    this.hide();
    return result;
  };

  render(): React.ReactElement {
    const { title, content, continueText, extraContent } = this.props;
    const { children } = this.props;
    const { open } = this.state;
    return (
      <>
        {children(this.show)}
        <Dialog
          fullWidth
          open={open}
          onClose={() => this.hide()}
          scroll='paper'
          aria-labelledby='form-dialog-title'
        >
          <DialogTitleWrapper>
            <DialogTitle id='scroll-dialog-title'>{title}</DialogTitle>
          </DialogTitleWrapper>
          <DialogContent>
            {extraContent ? (
              <Typography variant='body2' style={{ paddingBottom: '16px' }}>
                {extraContent}
              </Typography>
            ) : null}
            <Typography variant='body2'>{content}</Typography>
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
                {continueText || 'Continue'}
              </Button>
            </DialogActions>
          </DialogFooter>
        </Dialog>
      </>
    );
  }
}
