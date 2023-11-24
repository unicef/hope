import { useHistory } from 'react-router-dom';
import ListItemText from '@material-ui/core/ListItemText';
import Menu, { MenuProps } from '@material-ui/core/Menu';
import MenuItem from '@material-ui/core/MenuItem';
import { withStyles } from '@material-ui/core/styles';
import KeyboardArrowDownIcon from '@material-ui/icons/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@material-ui/icons/KeyboardArrowUp';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Button } from "@material-ui/core";
import { ProgramStatus, SurveyCategory } from '../../../__generated__/graphql';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { useProgramContext } from "../../../programContext";

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
  const { baseUrl } = useBaseUrl();
  const { selectedProgram } = useProgramContext();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

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
      <Button
        aria-controls='customized-menu'
        aria-haspopup='true'
        variant='contained'
        color='primary'
        onClick={handleClick}
        endIcon={anchorEl ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
        data-cy='button-new-survey'
        disabled={selectedProgram?.status !== ProgramStatus.Active}
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
        <StyledMenuItem data-cy='menu-item-rapid-pro'>
          <ListItemText
            data-cy='menu-item-rapid-pro-text'
            onClick={() => handleMenuItemClick(SurveyCategory.RapidPro)}
            primary={t('New Survey with Rapid Pro')}
          />
        </StyledMenuItem>
        <StyledMenuItem data-cy='menu-item-sms-text'>
          <ListItemText
            data-cy='menu-item-sms-text'
            onClick={() => handleMenuItemClick(SurveyCategory.Sms)}
            primary={t('New Survey with SMS')}
          />
        </StyledMenuItem>
        <StyledMenuItem data-cy='menu-item-manual'>
          <ListItemText
            data-cy='menu-item-manual-text'
            onClick={() => handleMenuItemClick(SurveyCategory.Manual)}
            primary={t('New Survey with Manual Process')}
          />
        </StyledMenuItem>
      </StyledMenu>
    </>
  );
};
