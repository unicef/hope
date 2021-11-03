import { Box, Button, DialogContent, DialogTitle } from '@material-ui/core';
import React, { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import styled from 'styled-components';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';
import { useIndividualFlexFieldsQuery } from '../../__generated__/graphql';

export const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

export const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;

export const StyledImage = styled.img`
  width: 100%;
  height: 100%;
  max-width: 700px;
  max-height: 700px;
  pointer-events: none;
`;
export const MiniImage = styled.div`
  height: 45px;
  width: 45px;
  cursor: pointer;
  background-position: center;
  background-repeat: no-repeat;
  background-image: url(${({ src }) => src});
  background-size: cover;
`;

export const StyledLink = styled(Link)`
  color: #000;
`;

export const IndividualFlexFieldPhotoModal = ({
  field,
}): React.ReactElement => {
  const { id } = useParams();
  const { data } = useIndividualFlexFieldsQuery({
    variables: { id },
    fetchPolicy: 'network-only',
  });
  const [dialogOpen, setDialogOpen] = useState(false);

  if (!data) {
    return null;
  }

  const { flexFields } = data.individual;
  const picUrl = flexFields[field.name];

  return picUrl ? (
    <>
      <MiniImage alt='photo' src={picUrl} onClick={() => setDialogOpen(true)} />
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        aria-labelledby='form-dialog-title'
      >
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>Photo</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <Box p={3}>
            <StyledImage alt='photo' src={picUrl} />
          </Box>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setDialogOpen(false)}>CANCEL</Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  ) : (
    <Box style={{ height: '100%' }} display='flex' alignItems='center'>
      -
    </Box>
  );
};
