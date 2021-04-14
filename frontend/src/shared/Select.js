/* eslint-disable */
import * as React from 'react';
import PropTypes from 'prop-types';
import { mergeClasses } from '@material-ui/styles';
import SelectInput from './SelectInput';
import formControlState from '@material-ui/core/FormControl/formControlState';
import useFormControl from '@material-ui/core/FormControl/useFormControl';
import withStyles from '@material-ui/core/styles/withStyles';
import ArrowDropDownIcon from '@material-ui/core/internal/svg-icons/ArrowDropDown';
import Input from '@material-ui/core/Input';
import NativeSelectInput from '@material-ui/core/NativeSelect/NativeSelectInput';
import FilledInput from '@material-ui/core/FilledInput';
import OutlinedInput from './OutlinedInput';

export const styles = (theme) => ({
    /* Styles applied to the select component `root` class. */
    root: {},
    /* Styles applied to the select component `select` class. */
    select: {
        '-moz-appearance': 'none', // Reset
        '-webkit-appearance': 'none', // Reset
        // When interacting quickly, the text can end up selected.
        // Native select can't be selected either.
        userSelect: 'none',
        borderRadius: 0, // Reset
        minWidth: 16, // So it doesn't collapse.
        cursor: 'pointer',
        '&:focus': {
            borderRadius: 0, // Reset Chrome style
            backgroundColor:'transparent'
        },
        // Remove IE 11 arrow
        '&::-ms-expand': {
            display: 'none',
        },
        '&$disabled': {
            cursor: 'default',
        },
        '&[multiple]': {
            height: 'auto',
        },
        '&:not([multiple]) option, &:not([multiple]) optgroup': {
            backgroundColor: theme.palette.background.paper,
        },
        '&&': {
            paddingRight: 24,
        },
    },
    /* Styles applied to the select component if `variant="filled"`. */
    filled: {
        '&&': {
            paddingRight: 32,
        },
    },
    /* Styles applied to the select component if `variant="outlined"`. */
    outlined: {
        borderRadius: theme.shape.borderRadius,
        '&&': {
            paddingRight: 32,
        },
    },
    /* Styles applied to the select component `selectMenu` class. */
    selectMenu: {
        height: 'auto', // Reset
        textOverflow: 'ellipsis',
        whiteSpace: 'nowrap',
        overflow: 'hidden',
    },
    /* Pseudo-class applied to the select component `disabled` class. */
    disabled: {},
    /* Styles applied to the icon component. */
    icon: {
        // We use a position absolute over a flexbox in order to forward the pointer events
        // to the input and to support wrapping tags..
        position: 'absolute',
        right: 0,
        top: 'calc(50% - 12px)', // Center vertically
        pointerEvents: 'none', // Don't block pointer events on the select under the icon.
        color: theme.palette.action.active,
        '&$disabled': {
            color: theme.palette.action.disabled,
        },
    },
    /* Styles applied to the icon component if the popup is open. */
    iconOpen: {
        transform: 'rotate(180deg)',
    },
    /* Styles applied to the icon component if `variant="filled"`. */
    iconFilled: {
        right: 7,
    },
    /* Styles applied to the icon component if `variant="outlined"`. */
    iconOutlined: {
        right: 7,
    },
});

const Select = React.forwardRef(function Select(props, ref) {
  const {
    autoWidth = false,
    children,
    classes,
    displayEmpty = false,
    IconComponent = ArrowDropDownIcon,
    id,
    input,
    inputProps,
    InputProps,
    label,
    labelId,
    labelWidth = 0,
    MenuProps,
    multiple = false,
    native = false,
    onClose,
    onOpen,
    open,
    renderValue,
    SelectDisplayProps,
    variant: variantProps = 'standard',
    ...other
  } = props;

  const inputComponent = native ? NativeSelectInput : SelectInput;

  const muiFormControl = useFormControl();
  const fcs = formControlState({
    props,
    muiFormControl,
    states: ['variant'],
  });

  const variant = fcs.variant || variantProps;

  const InputComponent =
    input ||
    {
      standard: <Input />,
      outlined: <OutlinedInput label={label} labelWidth={labelWidth} />,
      filled: <FilledInput />,
    }[variant];
  return React.cloneElement(InputComponent, {
    // Most of the logic is implemented in `SelectInput`.
    // The `Select` component is a simple API wrapper to expose something better to play with.
    inputComponent,
    ...InputProps,
    inputProps: {
      children,
      IconComponent,
      variant,
      type: undefined, // We render a select. We can ignore the type provided by the `Input`.
      multiple,
      ...(native
        ? { id }
        : {
            autoWidth,
            displayEmpty,
            labelId,
            MenuProps,
            onClose,
            onOpen,
            open,
            renderValue,
            SelectDisplayProps: { id, ...SelectDisplayProps },
          }),
      ...inputProps,
      classes: inputProps
        ? mergeClasses({
            baseClasses: classes,
            newClasses: inputProps.classes,
            Component: Select,
          })
        : classes,
      ...(input ? input.props.inputProps : {}),
    },
    ref,
    ...other,
  });
});

Select.propTypes = {
  // ----------------------------- Warning --------------------------------
  // | These PropTypes are generated from the TypeScript type definitions |
  // |     To update them edit the d.ts file and run "yarn proptypes"     |
  // ----------------------------------------------------------------------
  /**
   * If `true`, the width of the popover will automatically be set according to the items inside the
   * menu, otherwise it will be at least the width of the select input.
   */
  autoWidth: PropTypes.bool,
  /**
   * The option elements to populate the select with.
   * Can be some `MenuItem` when `native` is false and `option` when `native` is true.
   *
   * ⚠️The `MenuItem` elements **must** be direct descendants when `native` is false.
   */
  children: PropTypes.node,
  /**
   * Override or extend the styles applied to the component.
   * See [CSS API](#css) below for more details.
   */
  classes: PropTypes.object,
  /**
   * The default element value. Use when the component is not controlled.
   */
  defaultValue: PropTypes.any,
  /**
   * If `true`, a value is displayed even if no items are selected.
   *
   * In order to display a meaningful value, a function should be passed to the `renderValue` prop which returns the value to be displayed when no items are selected.
   * You can only use it when the `native` prop is `false` (default).
   */
  displayEmpty: PropTypes.bool,
  /**
   * The icon that displays the arrow.
   */
  IconComponent: PropTypes.elementType,
  /**
   * The `id` of the wrapper element or the `select` elment when `native`.
   */
  id: PropTypes.string,
  /**
   * An `Input` element; does not have to be a material-ui specific `Input`.
   */
  input: PropTypes.element,
  /**
   * [Attributes](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#Attributes) applied to the `input` element.
   * When `native` is `true`, the attributes are applied on the `select` element.
   */
  inputProps: PropTypes.object,
  /**
   * See [OutlinedInput#label](/api/outlined-input/#props)
   */
  label: PropTypes.node,
  /**
   * The ID of an element that acts as an additional label. The Select will
   * be labelled by the additional label and the selected value.
   */
  labelId: PropTypes.string,
  /**
   * See [OutlinedInput#label](/api/outlined-input/#props)
   */
  labelWidth: PropTypes.number,
  /**
   * Props applied to the [`Menu`](/api/menu/) element.
   */
  MenuProps: PropTypes.object,
  /**
   * If `true`, `value` must be an array and the menu will support multiple selections.
   */
  multiple: PropTypes.bool,
  /**
   * If `true`, the component will be using a native `select` element.
   */
  native: PropTypes.bool,
  /**
   * Callback function fired when a menu item is selected.
   *
   * @param {object} event The event source of the callback.
   * You can pull out the new value by accessing `event.target.value` (any).
   * @param {object} [child] The react element that was selected when `native` is `false` (default).
   */
  onChange: PropTypes.func,
  /**
   * Callback fired when the component requests to be closed.
   * Use in controlled mode (see open).
   *
   * @param {object} event The event source of the callback.
   */
  onClose: PropTypes.func,
  /**
   * Callback fired when the component requests to be opened.
   * Use in controlled mode (see open).
   *
   * @param {object} event The event source of the callback.
   */
  onOpen: PropTypes.func,
  /**
   * Control `select` open state.
   * You can only use it when the `native` prop is `false` (default).
   */
  open: PropTypes.bool,
  /**
   * Render the selected value.
   * You can only use it when the `native` prop is `false` (default).
   *
   * @param {any} value The `value` provided to the component.
   * @returns {ReactNode}
   */
  renderValue: PropTypes.func,
  /**
   * Props applied to the clickable div element.
   */
  SelectDisplayProps: PropTypes.object,
  /**
   * The input value. Providing an empty string will select no options.
   * This prop is required when the `native` prop is `false` (default).
   * Set to an empty string `''` if you don't want any of the available options to be selected.
   *
   * If the value is an object it must have reference equality with the option in order to be selected.
   * If the value is not an object, the string representation must match with the string representation of the option in order to be selected.
   */
  value: PropTypes.any,
  /**
   * The variant to use.
   */
  variant: PropTypes.oneOf(['filled', 'outlined', 'standard']),
};

Select.muiName = 'Select';

export default withStyles(styles, { name: 'MuiSelect' })(Select);
