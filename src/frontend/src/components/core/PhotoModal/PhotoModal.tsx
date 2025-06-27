import { Box, Button, DialogContent, IconButton } from '@mui/material';
import { TransformWrapper, TransformComponent } from 'react-zoom-pan-pinch';
import CloseIcon from '@mui/icons-material/Close';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import { Dialog } from '@containers/dialogs/Dialog';
import { PhotoModalFooter } from './PhotoModalFooter';
import { PhotoModalHeader } from './PhotoModalHeader';
import withErrorBoundary from '../withErrorBoundary';

export const StyledLink = styled(Link)`
  color: #000;
  width: 200px;
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
  display: inline-block;
`;

export const StyledImage = styled.img`
  width: 100%;
  height: 100%;
  max-width: 700px;
  max-height: 700px;
  pointer-events: none;
  transition: 0.4s ease-in-out;
`;

interface MiniImageProps {
  src?: string;
  alt?: string;
}

export const MiniImage = styled.div<MiniImageProps>`
  height: 45px;
  width: 45px;
  cursor: pointer;
  background-position: center;
  background-repeat: no-repeat;
  background-image: url(${({ src }) => src});
  background-size: cover;
`;

function PhotoModal({
  src,
  linkText,
  variant = 'picture',
  title = 'Photo',
  closeHandler,
  showRotate = true,
  alt = 'photo',
}: {
  src: string;
  alt?: string;
  linkText?: string;
  variant?: 'picture' | 'button' | 'link' | 'pictureClose';
  title?: string;
  closeHandler?;
  showRotate?: boolean;
}): ReactElement {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [turnAngle, setTurnAngle] = useState(90);
  const { t } = useTranslation();

  const matchVariant = (): ReactElement => {
    let element;
    switch (variant) {
      case 'picture':
        element = (
          <MiniImage
            data-cy="mini-image"
            alt={alt}
            src={src}
            onClick={() => setDialogOpen(true)}
          />
        );
        break;
      case 'button':
        element = (
          <Button
            data-cy="button-show-photo"
            color="primary"
            variant="outlined"
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
            data-cy="link-show-photo"
            onClick={() => {
              setDialogOpen(true);
            }}
            to={null}
          >
            {linkText}
          </StyledLink>
        );
        break;
      case 'pictureClose':
        element = (
          <Box display="flex" alignItems="center">
            <MiniImage
              data-cy="mini-image-close"
              alt={alt}
              src={src}
              onClick={() => setDialogOpen(true)}
            />
            <IconButton data-cy="close-icon" onClick={() => closeHandler()}>
              <CloseIcon />
            </IconButton>
          </Box>
        );
        break;
      default:
        element = (
          <MiniImage
            data-cy="mini-image"
            alt="photo"
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
        aria-labelledby="form-dialog-title"
      >
        <PhotoModalHeader
          title={title}
          turnAngle={turnAngle}
          setTurnAngle={setTurnAngle}
          showRotate={showRotate}
        />
        <DialogContent>
          <Box p={3}>
            <TransformWrapper>
              <TransformComponent>
                <StyledImage id="modalImg" alt="photo" src={src} />
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
}

export default withErrorBoundary(PhotoModal, 'PhotoModal');
