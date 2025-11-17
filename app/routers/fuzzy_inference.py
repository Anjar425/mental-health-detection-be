from fastapi import APIRouter, HTTPException, status
from ..schemas import FuzzyInferenceRequest, FuzzyInferenceAllResponse
from ..controllers import FuzzyInferenceController

router = APIRouter()

@router.post("/compute", response_model=FuzzyInferenceAllResponse)
def compute_fuzzy_inference_all(request: FuzzyInferenceRequest):
    try:
        # Validate input has all required Q1-Q42
        for i in range(1, 43):
            key = f"Q{i}"
            if key not in request.questionnaire_responses:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required questionnaire response: {key}"
                )
        print("test")
        # Compute for all categories
        results = FuzzyInferenceController().compute_all_inferences(input_values=request.questionnaire_responses)
        
        return {
            "depression": results["depression"],
            "anxiety": results["anxiety"],
            "stress": results["stress"],
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fuzzy inference computation failed: {str(e)}"
        )


# @router.post("/compute/{category}", response_model=FuzzyInferenceResponse)
# def compute_fuzzy_inference_category(
#     category: str,
#     request: FuzzyInferenceRequest,):

#     try:
#         # Validate category
#         valid_categories = ["depression", "anxiety", "stress"]
#         if category.lower() not in valid_categories:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=f"Invalid category: {category}. Must be one of: {', '.join(valid_categories)}"
#             )
        
#         # Validate input has all required Q1-Q42
#         for i in range(1, 43):
#             key = f"Q{i}"
#             if key not in request.questionnaire_responses:
#                 raise HTTPException(
#                     status_code=status.HTTP_400_BAD_REQUEST,
#                     detail=f"Missing required questionnaire response: {key}"
#                 )
        
#         # Compute for specific category
#         result = FuzzyInferenceController.compute_inference(
#             request.questionnaire_responses,
#             category.lower(),
#         )
        
#         return result
    
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Fuzzy inference computation failed: {str(e)}"
#         )


# @router.get("/health")
# def health_check(db: Session = Depends(get_db)):
#     """
#     Check fuzzy inference service health and database connectivity.
#     """
#     try:
#         # Verify database connection
#         db.execute("SELECT 1")
        
#         return {
#             "status": "healthy",
#             "service": "fuzzy-inference",
#             "database": "connected"
#         }
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
#             detail=f"Service unhealthy: {str(e)}"
#         )
