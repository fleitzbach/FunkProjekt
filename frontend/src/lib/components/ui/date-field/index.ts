import { DateField as DateFieldPrimitive } from 'bits-ui';

import Root from './date-field.svelte';
// import Segment from './date-field-segment.svelte';

const Segment = DateFieldPrimitive.Segment;
const Input = DateFieldPrimitive.Input;
const Label = DateFieldPrimitive.Label;

export {
	Root,
	Label,
	Input,
	Segment,
	//
	Root as DateField,
	Label as DateFieldLabel,
	Input as DateFieldInput,
	Segment as DateFieldSegment
};
