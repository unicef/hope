import { Box, Button, DialogContent, DialogTitle } from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';
import {
  ImportedIndividualNode,
  useImportedIndividualPhotosLazyQuery,
} from '../../__generated__/graphql';

const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;

const StyledImage = styled.img`
  max-width: 100%;
  max-height: 100%;
`;

interface ImportedIndividualPhotoModalProps {
  individual: ImportedIndividualNode;
}

export const ImportedIndividualPhotoModal = ({
  individual,
}: ImportedIndividualPhotoModalProps): React.ReactElement => {
  const { t } = useTranslation();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [getPhotos, { data }] = useImportedIndividualPhotosLazyQuery({
    variables: { id: individual?.id },
    fetchPolicy: 'network-only',
  });

  return (
    <>
      <Button
        color='primary'
        variant='outlined'
        onClick={() => {
          setDialogOpen(true);
          getPhotos();
        }}
      >
        {t('Show Photo')}
      </Button>
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        aria-labelledby='form-dialog-title'
      >
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>
            {t('Individual')}&apos;s {t('Photo')}
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <Box p={3}>
            <StyledImage alt={t('Individual')} src={data?.importedIndividual?.photo} />
          </Box>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setDialogOpen(false)}>{t('CANCEL')}</Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
};
