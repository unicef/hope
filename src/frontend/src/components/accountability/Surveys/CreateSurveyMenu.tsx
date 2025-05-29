import { styled } from '@mui/system';
import { Menu, MenuItem, Button, Tooltip, ListItemText } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import { ReactElement, useState, MouseEvent } from 'react';
import { useTranslation } from 'react-i18next';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useProgramContext } from '../../../programContext';
import { SurveyCategory } from '@generated/graphql';

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

export function CreateSurveyMenu(): ReactElement {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { baseUrl } = useBaseUrl();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const { isActiveProgram } = useProgramContext();

  const handleClick = (event: MouseEvent<HTMLElement>): void => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = (): void => {
    setAnchorEl(null);
  };

  const handleMenuItemClick = (category: string): void => {
    navigate({
      pathname: `/${baseUrl}/accountability/surveys/create/${category}`,
    });
  };

  return (
    <>
      {!isActiveProgram ? (
        <Tooltip title={t('Programme has to be active to create a Survey')}>
          <span>
            <Button
              aria-controls="customized-menu"
              aria-haspopup="true"
              variant="contained"
              color="primary"
              onClick={handleClick}
              endIcon={
                anchorEl ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />
              }
              data-cy="button-new-survey"
              disabled={!isActiveProgram}
            >
              {t('New Survey')}
            </Button>
          </span>
        </Tooltip>
      ) : (
        <Button
          aria-controls="customized-menu"
          aria-haspopup="true"
          variant="contained"
          color="primary"
          onClick={handleClick}
          endIcon={
            anchorEl ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />
          }
          data-cy="button-new-survey"
        >
          {t('New Survey')}
        </Button>
      )}

      <StyledMenu
        id="customized-menu"
        anchorEl={anchorEl}
        keepMounted
        open={Boolean(anchorEl)}
        onClose={handleClose}
      >
        <StyledMenuItem data-cy="menu-item-rapid-pro">
          <ListItemText
            data-cy="menu-item-rapid-pro-text"
            onClick={() => handleMenuItemClick(SurveyCategory.RapidPro)}
            primary={t('New Survey with Rapid Pro')}
          />
        </StyledMenuItem>
        <StyledMenuItem data-cy="menu-item-sms-text">
          <ListItemText
            data-cy="menu-item-sms-text"
            onClick={() => handleMenuItemClick(SurveyCategory.Sms)}
            primary={t('New Survey with SMS')}
          />
        </StyledMenuItem>
        <StyledMenuItem data-cy="menu-item-manual">
          <ListItemText
            data-cy="menu-item-manual-text"
            onClick={() => handleMenuItemClick(SurveyCategory.Manual)}
            primary={t('New Survey with Manual Process')}
          />
        </StyledMenuItem>
      </StyledMenu>
    </>
  );
}
