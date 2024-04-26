import { styled } from '@mui/system';
import { Menu, MenuItem, Button, Tooltip, ListItemText } from '@mui/material';
import { Link, useNavigate } from 'react-router-dom';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { SurveyCategory } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useProgramContext } from 'src/programContext';
import { ButtonTooltip } from '@components/core/ButtonTooltip';

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

export const CreateTPMenu = (): React.ReactElement => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { baseUrl } = useBaseUrl();
  const { isActiveProgram } = useProgramContext();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleClick = (event: React.MouseEvent<HTMLElement>): void => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = (): void => {
    setAnchorEl(null);
  };

  const handleMenuItemClick = (category: string): void => {
    navigate(`/${baseUrl}/target-population/create`, {
      state: { category },
    });
  };
  return (
    <>
      {!isActiveProgram ? (
        <ButtonTooltip
          variant="contained"
          color="primary"
          title={t(
            'Program has to be active to create a new Target Population',
          )}
          component={Link}
          to={`/${baseUrl}/target-population/create`}
          data-cy="button-target-population-create-new"
          disabled={!isActiveProgram}
        >
          Create new
        </ButtonTooltip>
      ) : (
        <>
          <Button
            aria-controls="customized-menu"
            aria-haspopup="true"
            variant="contained"
            color="primary"
            onClick={handleClick}
            endIcon={
              anchorEl ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />
            }
            data-cy="button-new-tp"
          >
            {t('Create New')}
          </Button>

          <StyledMenu
            id="customized-menu"
            anchorEl={anchorEl}
            keepMounted
            open={Boolean(anchorEl)}
            onClose={handleClose}
          >
            <StyledMenuItem data-cy="menu-item-filters">
              <ListItemText
                data-cy="menu-item-filters-text"
                onClick={() => handleMenuItemClick('filters')}
                primary={t('Use Filters')}
              />
            </StyledMenuItem>
            <StyledMenuItem data-cy="menu-item-ids">
              <ListItemText
                data-cy="menu-item-ids-text"
                onClick={() => handleMenuItemClick('ids')}
                primary={t('Use IDs')}
              />
            </StyledMenuItem>
          </StyledMenu>
        </>
      )}
    </>
  );
};
