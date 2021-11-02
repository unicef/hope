import { Box, Button, DialogContent, DialogTitle } from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';
import {
  IndividualNode,
  useIndividualPhotosLazyQuery,
} from '../../__generated__/graphql';
import {
  DialogFooter,
  DialogTitleWrapper,
  StyledImage,
} from './IndividualFlexFieldPhotoModal';

interface IndividualPhotoModalProps {
  individual: IndividualNode;
}

export const IndividualPhotoModal = ({
  individual,
}: IndividualPhotoModalProps): React.ReactElement => {
  const { t } = useTranslation();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [getPhotos, { data }] = useIndividualPhotosLazyQuery({
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
            <StyledImage alt={t('Individual')} src={data?.individual?.photo} />
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
