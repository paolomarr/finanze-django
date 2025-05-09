import React, { useRef, useState } from 'react';
import Card from 'react-bootstrap/Card';
// import ListGroup from "react-bootstrap/ListGroup";
import Form from "react-bootstrap/Form";
import Button from 'react-bootstrap/esm/Button';
import { t } from '@lingui/macro';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import fetchMovements from '../queries/fetchMovements';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCircleCheck, faCircleXmark, faPenToSquare } from '@fortawesome/free-solid-svg-icons';
import { Trans } from "@lingui/macro";
import mutateCategory from "../queries/mutateCategory";
import mutateSubcategory from "../queries/mutateSubcategory";
import Row from 'react-bootstrap/esm/Row';
import Col from 'react-bootstrap/esm/Col';
// import Alert from 'react-bootstrap/Alert';

const EditorPanel = ({ items, label, title, onMutateItem, submitErrors }) => {
    const defaultItem = {id: null, [label]:"", direction:-1};
    const [outItem, setOutItem] = useState(defaultItem);
    const [formChanged, setFormChanged] = useState(false);
    const [saveDisabled, setSaveDisabled] = useState(true);
    const itemValueRef = useRef(null);
    const itemDirectionRef = useRef(null);
    const formRef = useRef(null); // Reference for the Form

    const handleEditClick = (item) => {
        setOutItem(item);
        setFormChanged(true);
        itemValueRef.current.value = item[label] ?? "";
        if(itemDirectionRef.current!=null){
            itemDirectionRef.current.value = item.direction;
        }
        // Scroll to the top of the Form
        if (formRef.current) {
            formRef.current.scrollIntoView({ behavior: 'smooth' });
        }
        // Focus on the value field and select its text
        if (itemValueRef.current) {
            itemValueRef.current.focus();
            itemValueRef.current.select();
        }
    };
    const handleSubmitItem = () => {
        onMutateItem(outItem);
        setFormChanged(false);
    }
    const SubmitFeedbackComponent = ({errors}) => {
        let feedBackLabel = "";
        let feedBackIcon = null;
        if(formChanged || !errors){
            return <></>
        }else{
            if(Object.keys(errors).length == 0){
                feedBackLabel = t`Saved`;
                feedBackIcon = faCircleCheck;
            }else{
                feedBackLabel = t`Error`;
                feedBackIcon = faCircleXmark;
            }
        }
        return <>
                <span className='text-success'>{feedBackLabel}</span>{' '}<FontAwesomeIcon icon={feedBackIcon}/>
        </>
    }

    const saveLabel = outItem.id ? t`Update` : t`Add`;
    return (
        <Card className="shadow-lg">
            <Card.Body>
                <Card.Title>{title}</Card.Title>
                <div ref={formRef}> {/* Attach ref to the div containing the Form */}
                    <Form>
                        <Form.Group className="mb-3" controlId="formBasicEmail">
                            <Form.Label>Name</Form.Label>
                            <Form.Control
                                name={label}
                                ref={itemValueRef}
                                onChange={(event) => {
                                    const value = event.target.value;
                                    setOutItem({ ...outItem, [label]: value });
                                    setFormChanged(true);
                                    setSaveDisabled(value.length === 0);
                                }}
                            />
                        </Form.Group>
                        { label == "category" ?
                        <Form.Group className="mb-3" controlId="formBasicEmail">
                            <Form.Label>Direction</Form.Label>
                            <Form.Select 
                            name="direction"
                            ref={itemDirectionRef}
                            onChange={(event)=> {
                                setOutItem({...outItem, direction: event.target.value})
                                setFormChanged(true);
                                }}>
                                <option value={1}><Trans>Earnings</Trans></option>
                                <option value={-1}><Trans>Expenses</Trans></option>
                            </Form.Select>
                        </Form.Group> : null 
                        }
                    </Form>
                    { outItem.id ? 
                    <Button type='button' variant='secondary' onClick={() => handleEditClick(defaultItem)}><Trans>Cancel</Trans></Button> 
                    : null}{' '}
                    <Button type="button" onClick={handleSubmitItem} disabled={saveDisabled}>{saveLabel}</Button>{' '}
                    <SubmitFeedbackComponent errors={submitErrors}/>
                </div>
                {items.length > 0 ? (
                    <div className='mt-2 row row-cols-1 row-cols-md-3 row-cols-lg-4'>
                        {items.filter((item)=> item.direction != 0 && item[label] != "BALANCE" && item[label].length > 0).map((item)=> {
                            const color_class = label == "category" ? (item.direction == -1 ? "text-expenses" : "text-earnings") : "";
                            const active_class = item.id == outItem.id ? "bg-secondary-subtle" : "";
                            return <div key={item.id} className={`col ${active_class} ${color_class}`}>
                                <FontAwesomeIcon 
                                        icon={faPenToSquare} 
                                        onClick={() => handleEditClick(item)} 
                                        style={{ cursor: 'pointer', marginRight: '10px' }} 
                                    />
                                    {item[label]}
                                </div>
                        })}
                    </div> 
                ) : (
                    <div>{t`No data`}</div>
                )}
            </Card.Body>
        </Card>
    );
};

const CategoryManager = () => {
    const { data: categoryData } = useQuery({
        queryKey: ["categories"],
        queryFn: fetchMovements,
        placeholderData: [],
    });
    const { data: subcategoryData } = useQuery({
        queryKey: ["subcategories"],
        queryFn: fetchMovements,
        placeholderData: [],
    });
    const queryClient = useQueryClient();
    const [categoryMutationError, setCategoryMutationError] = useState(null);
    const [subcategoryMutationError, setSubCategoryMutationError] = useState(null);
    const { mutate: categoryMutationMutate} = useMutation({
        mutationFn: ({item, label, _delete}) => {
            let _mutationFunction = mutateCategory;
            if(label == "subcategory"){
                _mutationFunction = mutateSubcategory;
            }
            return _mutationFunction({[label]:item, _delete: _delete});
        },
        onSuccess: (result, {item, label, _delete}) => {
            const queryKey = label == "category" ? ["categories"] : ["subcategories"];
            queryClient.setQueryData(queryKey, (oldData) => {
                if(item.id){ // DELETE or PUT
                    const itemIdx = oldData.findIndex((oitem)=> oitem.id === item.id);
                    if(itemIdx>=0){
                        if(_delete){
                            oldData.splice(itemIdx, 1); // remove
                        }else{
                            oldData.splice(itemIdx, 1, item); // replace
                        }
                    }
                }else { // POST
                    oldData.push(result);
                }
                return oldData;
            });
            // reset form components fields
            if(label == "category"){
                setCatKey(catKey + 1);
                setCategoryMutationError({});
            }else{
                setSubcatKey(subcatKey + 1);
                setSubCategoryMutationError({});
            }
        },
        onError: (error, {label}) => {
            if(label == "category"){
                setCategoryMutationError(error);
            }else{
                setSubCategoryMutationError(error);
            }
        }
    });
    const onMutateItem = (item, label) => {
        var todelete = false;
        if(item.id){ // edit or delete
            if(item[label]){ // object label defined, so it's an edit
                todelete = false;
            }else{
                todelete = true;
            }
        }
        categoryMutationMutate({item:item, label: label, _delete: todelete});
    }
    const [catKey, setCatKey] = useState(0);
    const [subcatKey, setSubcatKey] = useState(0);
    return (
        <>
            <div className='my-2'>
                <Row className="justify-content-center">
                    <Col className='md-8'>
                        <EditorPanel key={catKey} submitErrors={categoryMutationError} onMutateItem={(item)=> onMutateItem(item, "category")} items={categoryData} label="category" title={t`Categories`} />
                    </Col>
                </Row>
            </div>
            <div className='my-2'>
                <Row className="justify-content-center">
                    <Col className='md-8'>
                        <EditorPanel key={subcatKey} submitErrors={subcategoryMutationError} onMutateItem={(item)=> onMutateItem(item, "subcategory")} items={subcategoryData} label="subcategory" title={t`Subcategories`} />
                    </Col>
                </Row>
            </div>
        </>
    );
};

export default CategoryManager;
