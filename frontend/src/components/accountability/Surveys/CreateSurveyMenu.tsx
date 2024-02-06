import { useHistory } from 'react-router-dom';
import ListItemText from '@mui/material/ListItemText';
import Menu, { MenuProps } from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import { withStyles } from '@mui/material/styles';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Button, Tooltip } from '@mui/material';
import { SurveyCategory } from '../../../__generated__/graphql';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { useProgramContext } from '../../../programContext';

const StyledMenu = withStyles({
  paper: {
    border: '1px solid #d3d4d5',
  },
})((props: MenuProps) => (
  <Menu
    elevation={0}
    getContentAnchorEl={null}
    anchorOrigin={{
      vertical: 'bottom',
      horizontal: 'center',
    }}
    transformOrigin={{
      vertical: 'top',
      horizontal: 'center',
    }}
    {...props}
  />
));

const StyledMenuItem = withStyles((theme) => ({
  root: {
    '&:focus': {
      backgroundColor: theme.palette.primary.main,
      '& .MuiListItemIcon-root, & .MuiListItemText-primary': {
        color: theme.palette.common.white,
      },
    },
  },
}))(MenuItem);

export function CreateSurveyMenu(): React.ReactElement {
  const { t } = useTranslation();
  const history = useHistory();
  const { baseUrl } = useBaseUrl();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const { isActiveProgram } = useProgramContext();

  const handleClick = (event: React.MouseEvent<HTMLElement>): void => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = (): void => {
    setAnchorEl(null);
  };

  const handleMenuItemClick = (category: string): void => {
    history.push({
      pathname: `/${baseUrl}/accountability/surveys/create/${category}`,
    });
  };

  return (
    <>
      {!isActiveProgram ? (
        <Tooltip title={t('Program has to be active to create a Survey')}>
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
