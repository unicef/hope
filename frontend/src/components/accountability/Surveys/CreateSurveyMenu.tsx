import Button from '@material-ui/core/Button';
import { useHistory } from 'react-router-dom';
import ListItemText from '@material-ui/core/ListItemText';
import Menu, { MenuProps } from '@material-ui/core/Menu';
import MenuItem from '@material-ui/core/MenuItem';
import { withStyles } from '@material-ui/core/styles';
import KeyboardArrowDownIcon from '@material-ui/icons/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@material-ui/icons/KeyboardArrowUp';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { SurveyCategory } from '../../../__generated__/graphql';

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

export const CreateSurveyMenu = (): React.ReactElement => {
  const { t } = useTranslation();
  const history = useHistory();
  const businessArea = useBusinessArea();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleClick = (event: React.MouseEvent<HTMLElement>): void => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = (): void => {
    setAnchorEl(null);
  };

  const handleMenuItemClick = (category: string): void => {
    history.push({
      pathname: `/${businessArea}/accountability/surveys/create`,
      state: {
        category,
      },
    });
  };

  return (
    <>
      <Button
        aria-controls='customized-menu'
        aria-haspopup='true'
        variant='contained'
        color='primary'
        onClick={handleClick}
        endIcon={anchorEl ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
        data-cy='button-new-survey'
      >
        {t('New Survey')}
      </Button>
      <StyledMenu
        id='customized-menu'
        anchorEl={anchorEl}
        keepMounted
        open={Boolean(anchorEl)}
        onClose={handleClose}
      >
        <StyledMenuItem>
          <ListItemText
            data-cy='menu-item-rapid-pro'
            onClick={() => handleMenuItemClick(SurveyCategory.RapidPro)}
            primary={t('New Survey with Rapid Pro')}
          />
        </StyledMenuItem>
        <StyledMenuItem>
          <ListItemText
            data-cy='menu-item-sms'
            onClick={() => handleMenuItemClick(SurveyCategory.Sms)}
            primary={t('New Survey with SMS')}
          />
        </StyledMenuItem>
        <StyledMenuItem>
          <ListItemText
            data-cy='menu-item-manual'
            onClick={() => handleMenuItemClick(SurveyCategory.Manual)}
            primary={t('New Survey with Manual Process')}
          />
        </StyledMenuItem>
      </StyledMenu>
    </>
  );
};
