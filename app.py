import streamlit as st
import json
from datetime import datetime

# Initialize in-memory data storage
recommendation_types = {
    1: {
        "name": "General",
        "description": "General recommendation",
        "schema_definition": {
            "description": "string",
            "source": "string"
        }
    },
    2: {
        "name": "StorageAlert",
        "description": "Alerts for storage issues",
        "schema_definition": {
            "description": "string",
            "hdfs_path": "string",
            "usage_gb": "number"
        }
    },
    3: {
        "name": "PerformanceTuning",
        "description": "Performance improvement advice",
        "schema_definition": {
            "description": "string",
            "cpu_usage": "number",
            "duration": "string"
        }
    }
}

# Add this near the top of your file after the recommendation_types definition
CONSUMERS = [
    "CONSUMER_001",
    "CONSUMER_002",
    "CONSUMER_003",
    "CONSUMER_004",
    "CONSUMER_005",
    "CONSUMER_ABC",
    "CONSUMER_XYZ",
    "CONSUMER_TEST",
]

# Add these near the top of your file after CONSUMERS
PRODUCTS = [
    "PRODUCT_A",
    "PRODUCT_B",
    "PRODUCT_C",
    "PRODUCT_D",
]

# Define deployments per consumer and product
DEPLOYMENTS = {
    "CONSUMER_001": {
        "PRODUCT_A": ["DEP_001", "DEP_002", "DEP_003"],
        "PRODUCT_B": ["DEP_004", "DEP_005"],
        "PRODUCT_C": ["DEP_006"]
    },
    "CONSUMER_002": {
        "PRODUCT_A": ["DEP_007", "DEP_008"],
        "PRODUCT_B": ["DEP_009", "DEP_010", "DEP_011"]
    },
    # Add more consumers and their deployments
}

# At the top after imports
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = []

# Add these constants at the top
IMPACT_LEVELS = {
    1: "Very Low",
    2: "Low",
    3: "Medium",
    4: "High",
    5: "Very High"
}

PRIORITY_LEVELS = {
    1: "Very Low",
    2: "Low",
    3: "Medium",
    4: "High",
    5: "Critical"
}

STATUSES = {
    "pending": "Pending",
    "in_progress": "In Progress",
    "done": "Done",
    "closed": "Closed"
}

# Function to add a new recommendation
def add_recommendation(consumer_id, product_id, type_id, additional_data, impact, priority,deployment_id):
    recommendation = {
        "recommendation_id": len(st.session_state.recommendations) + 1,
        "creation_time": datetime.now(),
        "consumer_id": consumer_id,
        "product_id": product_id,
        "type_id": type_id,
        "impact": impact,
        "priority": priority,
        "deployment_id": deployment_id,
        "additional_data": additional_data,
        "status": "pending",
        "status_history": [{
            "timestamp": datetime.now(),
            "status": "pending",
            "note": "Initial creation"
        }]
    }
    st.session_state.recommendations.append(recommendation)

# Streamlit application
st.title("Recommendations Management")

# Create tabs for different functionalities
tabs = st.tabs(["Create Recommendation", "View Recommendations"])

# Create a Recommendation
with tabs[0]:
    st.header("Create a Recommendation")
    
    # Recommendation type selection
    st.subheader("1. Select Recommendation Type")
    type_id = st.selectbox("Recommendation Type", options=list(recommendation_types.keys()), 
                          format_func=lambda x: f"{recommendation_types[x]['name']} - {recommendation_types[x]['description']}")
    
    # Show selected type description
    st.info(f"📋 You selected: **{recommendation_types[type_id]['name']}**\n\n"
            f"This type requires the following information:")
    
    st.subheader("2. Enter Basic Information")
    consumer_id = st.selectbox(
        "Consumer ID",
        options=CONSUMERS,
        help="Select the consumer for this recommendation"
    )

    # Get available products for this consumer
    available_products = list(DEPLOYMENTS.get(consumer_id, {}).keys())
    product_id = st.selectbox(
        "Product ID",
        options=available_products if available_products else PRODUCTS,
        help="Select the product for this consumer"
    )

    # Get available deployments for this consumer and product
    available_deployments = DEPLOYMENTS.get(consumer_id, {}).get(product_id, [])
    deployment_id = st.selectbox(
        "Deployment ID",
        options=available_deployments,
        help="Select the deployment for this consumer and product"
    )

    # Initialize session state for additional data
    if 'additional_data' not in st.session_state:
        st.session_state.additional_data = {}
    
    # Clear previous additional data for new type selection
    if 'last_type_id' not in st.session_state or st.session_state.last_type_id != type_id:
        st.session_state.additional_data = {}
        st.session_state.last_type_id = type_id
    
    st.subheader("3. Set Impact and Priority")
    col1, col2 = st.columns(2)
    
    with col1:
        impact = st.radio(
            "Impact Level",
            options=list(IMPACT_LEVELS.keys()),
            format_func=lambda x: f"{x} - {IMPACT_LEVELS[x]}",
            horizontal=True,
            help="How significant is the impact of this recommendation?"
        )
    
    with col2:
        priority = st.radio(
            "Priority Level",
            options=list(PRIORITY_LEVELS.keys()),
            format_func=lambda x: f"{x} - {PRIORITY_LEVELS[x]}",
            horizontal=True,
            help="How urgent is this recommendation?"
        )

    st.subheader("3. Enter Type-Specific Details")
    schema = recommendation_types[type_id]["schema_definition"]
    
    # Handle description field first
    if "description" in schema:
        field_label = "Description"
        st.session_state.additional_data["description"] = st.text_area(
            f"Enter {field_label}", 
            st.session_state.additional_data.get("description", ""),
            help="Provide a detailed description of the recommendation"
        )
    
    # Handle other fields
    for field, field_type in schema.items():
        if field == "description":  # Skip description as it's already handled
            continue
            
        field_label = field.replace('_', ' ').title()
        if field_type == "string":
            st.session_state.additional_data[field] = st.text_input(f"Enter {field_label}", 
                st.session_state.additional_data.get(field, ""))
        elif field_type == "number":
            try:
                current_value = float(st.session_state.additional_data.get(field, 0.0))
            except (TypeError, ValueError):
                current_value = 0.0
                
            value = st.number_input(
                f"Enter {field_label}", 
                value=0.0,
                min_value=0.0,
                max_value=float(1e6),
                step=0.1
            )
            st.session_state.additional_data[field] = float(value)

    if st.button("Create Recommendation"):
        if consumer_id and product_id and deployment_id:
            add_recommendation(
                consumer_id=consumer_id,
                product_id=product_id,
                type_id=type_id,
                impact=impact,
                priority=priority,
                deployment_id=deployment_id,
                additional_data=st.session_state.additional_data
            )
            # Store success message in session state
            st.session_state.show_success = True
            # Clear form fields after successful submission
            st.session_state.additional_data = {}
            st.rerun()
        else:
            st.error("Please fill in all required fields.")

    # Show success message if it exists in session state
    if 'show_success' in st.session_state and st.session_state.show_success:
        st.success("Recommendation created successfully!")
        # Clear the success message flag
        del st.session_state.show_success

# View Recommendations
with tabs[1]:
    st.header("View Recommendations")
    
    # Add toggle for hiding completed recommendations
    hide_completed = st.toggle(
        "Hide completed recommendations",
        value=True,
        help="Hide recommendations with 'Done' or 'Closed' status"
    )
    
    # Filtering options with dropdowns
    filter_consumer_id = st.selectbox(
        "Filter by Consumer ID (optional)",
        options=[""] + CONSUMERS,
        format_func=lambda x: "All Consumers" if x == "" else x,
    ).strip()
    
    # Get available products for selected consumer
    available_filter_products = [""] + (list(DEPLOYMENTS.get(filter_consumer_id, {}).keys()) if filter_consumer_id else PRODUCTS)
    filter_product_id = st.selectbox(
        "Filter by Product ID (optional)",
        options=available_filter_products,
        format_func=lambda x: "All Products" if x == "" else x,
    ).strip()
    
    # Get available deployments for selected consumer and product
    available_filter_deployments = [""]
    if filter_consumer_id and filter_product_id:
        available_filter_deployments.extend(DEPLOYMENTS.get(filter_consumer_id, {}).get(filter_product_id, []))
    
    filter_deployment_id = st.selectbox(
        "Filter by Deployment ID (optional)",
        options=available_filter_deployments,
        format_func=lambda x: "All Deployments" if x == "" else x,
    ).strip()
    
    filtered_recommendations = st.session_state.recommendations.copy()
    
    # Apply hide completed filter first if enabled
    if hide_completed:
        filtered_recommendations = [
            rec for rec in filtered_recommendations 
            if rec['status'] not in ['done', 'closed']
        ]
        st.write(f"Active recommendations: {len(filtered_recommendations)}")

    # Debug information
    st.write("Total recommendations:", len(filtered_recommendations))
    
    # Apply filters if provided
    if filter_consumer_id:  # Only filter if a consumer is selected
        filtered_recommendations = [
            rec for rec in filtered_recommendations 
            if filter_consumer_id == rec['consumer_id']
        ]
        st.write(f"Results after consumer filter: {len(filtered_recommendations)}")
    if filter_deployment_id:
        filtered_recommendations = [
            rec for rec in filtered_recommendations 
            if filter_consumer_id == rec['deployment_id']  # Exact match for now
        ]
        st.write(f"Results after Deployment filter: {len(filtered_recommendations)}")

    if filter_product_id:
        filtered_recommendations = [
            rec for rec in filtered_recommendations 
            if filter_product_id == rec['product_id']  # Exact match for now
        ]
        st.write(f"Results after product filter: {len(filtered_recommendations)}")
    
    # Optionally, add sorting in the View tab
    sort_by = st.radio(
        "Sort by:",
        options=["Creation Time", "Impact", "Priority"],
        horizontal=True
    )
    
    # Display results
    if filtered_recommendations:
        if sort_by == "Impact":
            filtered_recommendations.sort(key=lambda x: x['impact'], reverse=True)
        elif sort_by == "Priority":
            filtered_recommendations.sort(key=lambda x: x['priority'], reverse=True)
        else:  # Creation Time
            filtered_recommendations.sort(key=lambda x: x['creation_time'], reverse=True)
            
        for rec in filtered_recommendations:
            with st.expander(f"Recommendation {rec['recommendation_id']} - {rec['consumer_id']}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write("Impact:", f"**{IMPACT_LEVELS[rec['impact']]}** ({rec['impact']})")
                    st.write(f"Creation Time: {rec['creation_time']}")
                    st.write(f"Consumer ID: {rec['consumer_id']}")
                
                with col2:
                    st.write("Priority:", f"**{PRIORITY_LEVELS[rec['priority']]}** ({rec['priority']})")
                    st.write(f"Product ID: {rec['product_id']}")
                    st.write(f"Recommendation Type: {recommendation_types[rec['type_id']]['name']}")
                
                with col3:
                    st.write("Current Status:", f"**{STATUSES[rec['status']]}**")
                    new_status = st.selectbox(
                        "Update Status",
                        options=list(STATUSES.keys()),
                        format_func=lambda x: STATUSES[x],
                        key=f"status_{rec['recommendation_id']}"
                    )
                    
                    note = st.text_area(
                        "Add Note (required for status change)",
                        key=f"note_{rec['recommendation_id']}"
                    )
                    
                    if st.button("Update Status", key=f"update_{rec['recommendation_id']}"):
                        if note.strip():
                            if new_status != rec['status']:
                                rec['status_history'].append({
                                    "timestamp": datetime.now(),
                                    "status": new_status,
                                    "note": note.strip()
                                })
                                rec['status'] = new_status
                                st.success("Status updated successfully!")
                                st.rerun()
                        else:
                            st.error("Please add a note to explain the status change")
                
                if 'description' in rec['additional_data']:
                    st.write("Description:")
                    st.info(rec['additional_data']['description'])
                
                st.write("Additional Data:")
                other_data = {k: v for k, v in rec['additional_data'].items() if k != 'description'}
                st.json(other_data)
                
                # Display status history
                st.write("Status History:")
                for history in reversed(rec['status_history']):
                    st.write(f"**{STATUSES[history['status']]}** - {history['timestamp']}")
                    st.write(f"Note: {history['note']}")
                    st.write("---")
    else:
        if len(st.session_state.recommendations) == 0:
            st.warning("No recommendations have been created yet.")
        else:
            st.warning("No recommendations match the current filters.")



