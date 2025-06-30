import { useBaseUrl } from '@hooks/useBaseUrl';
import EditIcon from '@mui/icons-material/EditRounded';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import { Button, ListItemText, Menu, MenuItem } from '@mui/material';
import { styled } from '@mui/system';
import { ProgramDetail } from '@restgenerated/models/ProgramDetail';
import { MouseEvent, ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';

const StyledMenu = styled(Menu)(() => ({
  '.MuiPaper-root': {
    border: '1px solid #d3d4d5',
  },
}));

const StyledMenuItem = styled(MenuItem)(({ theme }) => ({
  '&:focus': {
    backgroundColor: theme.palette.primary.main,
    '& .MuiListItemIcon-root, & .MuiListItemText-primary': {
      color: theme.palette.common.white,
    },
  },
}));

interface EditProgramMenuProps {
  program: ProgramDetail;
}

export const EditProgramMenu = ({
  program,
}: EditProgramMenuProps): ReactElement => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { baseUrl } = useBaseUrl();

  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleClick = (event: MouseEvent<HTMLElement>): void => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = (): void => {
    setAnchorEl(null);
  };

  const handleMenuItemClick = (option: string): void => {
    navigate(`/${baseUrl}/edit/${program.slug}`, { state: { option } });
  };

  return (
    <>
      <Button
        aria-controls="customized-menu"
        aria-haspopup="true"
        variant="outlined"
        color="primary"
        onClick={handleClick}
        startIcon={<EditIcon />}
        endIcon={anchorEl ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
        data-cy="button-edit-program"
      >
        {t('Edit Programme')}
      </Button>

      <StyledMenu
        id="customized-menu"
        anchorEl={anchorEl}
        keepMounted
        open={Boolean(anchorEl)}
        onClose={handleClose}
      >
        <StyledMenuItem data-cy="menu-item-edit-details">
          <ListItemText
            data-cy="menu-item-edit-details-text"
            onClick={() => handleMenuItemClick('details')}
            primary={t('Edit Programme Details')}
          />
        </StyledMenuItem>
        <StyledMenuItem data-cy="menu-item-edit-partners">
          <ListItemText
            data-cy="menu-item-edit-partners-text"
            onClick={() => handleMenuItemClick('partners')}
            primary={t('Edit Programme Partners')}
          />
        </StyledMenuItem>
      </StyledMenu>
    </>
  );
};
