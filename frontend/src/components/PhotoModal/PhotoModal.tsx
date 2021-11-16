import { Box, Button, DialogContent, IconButton } from '@material-ui/core';
import { TransformWrapper, TransformComponent } from 'react-zoom-pan-pinch';
import CloseIcon from '@material-ui/icons/Close';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import { Dialog } from '../../containers/dialogs/Dialog';
import { PhotoModalFooter } from './PhotoModalFooter';
import { PhotoModalHeader } from './PhotoModalHeader';

export const StyledLink = styled(Link)`
  color: #000;
`;

export const StyledImage = styled.img`
  width: 100%;
  height: 100%;
  max-width: 700px;
  max-height: 700px;
  pointer-events: none;
  transition: 0.4s ease-in-out;
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

export const PhotoModal = ({
  src,
  linkText,
  variant = 'picture',
  title = 'Photo',
  closeHandler,
}: {
  src: string;
  linkText?: string;
  variant?: 'picture' | 'button' | 'link' | 'pictureClose';
  title?: string;
  closeHandler?;
}): React.ReactElement => {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [turnAngle, setTurnAngle] = useState(90);
  const { t } = useTranslation();

  const matchVariant = (): React.ReactElement => {
    let element;
    switch (variant) {
      case 'picture':
        element = (
          <MiniImage
            alt='photo'
            src={src}
            onClick={() => setDialogOpen(true)}
          />
        );
        break;
      case 'button':
        element = (
          <Button
            color='primary'
            variant='outlined'
            onClick={() => {
              setDialogOpen(true);
            }}
          >
            {t('Show Photo')}
          </Button>
        );
        break;
      case 'link':
        element = (
          <StyledLink
            onClick={() => {
              setDialogOpen(true);
            }}
          >
            {linkText}
          </StyledLink>
        );
        break;
      case 'pictureClose':
        element = (
          <Box display='flex' alignItems='center'>
            <MiniImage
              alt='photo'
              src={src}
              onClick={() => setDialogOpen(true)}
            />
            <IconButton onClick={() => closeHandler()}>
              <CloseIcon />
            </IconButton>
          </Box>
        );
        break;
      default:
        element = (
          <MiniImage
            alt='photo'
            src={src}
            onClick={() => setDialogOpen(true)}
          />
        );
    }
    return element;
  };

  return (
    <>
      {matchVariant()}
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        aria-labelledby='form-dialog-title'
      >
        <PhotoModalHeader
          title={title}
          turnAngle={turnAngle}
          setTurnAngle={setTurnAngle}
        />
        <DialogContent>
          <Box p={3}>
            <TransformWrapper>
              <TransformComponent>
                <StyledImage id='modalImg' alt='photo' src={src} />
              </TransformComponent>
            </TransformWrapper>
          </Box>
        </DialogContent>
        <PhotoModalFooter
          setTurnAngle={setTurnAngle}
          setDialogOpen={setDialogOpen}
        />
      </Dialog>
    </>
  );
};
