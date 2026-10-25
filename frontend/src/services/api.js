import axios from "axios";


const API = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
    headers: {
        "Content-Type": "application/json"
    }
});


export async function startResearch(
    topic,
    maxRevisions = 2
) {

    const response = await API.post(
        "/research",
        {
            topic,
            max_revisions: maxRevisions
        }
    );

    return response.data;
}


export async function getResearch(
    researchId
) {

    const response = await API.get(
        `/research/${researchId}`
    );

    return response.data;
}


export async function healthCheck() {

    const response = await API.get(
        "/health"
    );

    return response.data;
}
