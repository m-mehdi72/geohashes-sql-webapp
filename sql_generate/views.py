import os
import tempfile
from django.shortcuts import render
from django.http import HttpResponse
from .forms import QueryForm, UploadFileForm, PolygonForm
from .sql_script import generate_query
from .geohash import generate_hash_csv_response, process_file
from .lat_long_script import generate_coordinates_csv_response ,extract_coordinates
from .polygon_query import polygon_query_script

# Create your views here.
def sql(request):
    if request.method == 'POST':
        form = QueryForm(request.POST)
        if form.is_valid():
            table_name = form.cleaned_data['table_name']
            column_name = form.cleaned_data['column_name']
            values = form.cleaned_data['values']
            entries = values.split('\n')  
            entries = [entry.strip() for entry in entries if entry.strip()]  
            query = generate_query(table_name, column_name, entries)
            return render(request, 'sql_generate/sql_generation.html', {'form': form, 'query': query})
        else:
            print("Form is invalid:", form.errors)
    else:
        form = QueryForm()
    return render(request, 'sql_generate/sql_generation.html', {'form': form})

def hash(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            file_content = uploaded_file.read()
            # Save file content to a temporary file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name

            processed_data = process_file(temp_file_path)
            os.unlink(temp_file_path)
            formatted_data = ''
            # for name, value in processed_data:
            #     formatted_data += f"{name}: {value}\n"
            return render(request, 'sql_generate/geojson_to_geohashes.html', {
                'processed_data': processed_data,
                'feedback' : "Your file has been Uploaded",
                'form':form
                })
    else:
        form = UploadFileForm()
    return render(request, 'sql_generate/geojson_to_geohashes.html', {'form': form})

def download_hash_csv(request):
    if request.method == 'POST':
        processed_data = request.POST.get('processed_data', '')
        if processed_data:
            response = generate_hash_csv_response(processed_data)
            if response:
                # Set the appropriate content type for CSV files
                response['Content-Type'] = 'text/csv'
                # Optionally, set a filename for the downloaded CSV file
                response['Content-Disposition'] = 'attachment; filename="geo_hashes.csv"'
                return response
            else:
                return HttpResponse("Error generating CSV. Please try again.")
        else:
            return HttpResponse("Processed data not found in the request. Please try again.")
    else:
        return HttpResponse("Invalid request method. This endpoint only accepts POST requests.")

def coordinates_generator(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            file_content = uploaded_file.read()
            # Save file content to a temporary file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name

            coordinates, messages = extract_coordinates(temp_file_path)
            os.unlink(temp_file_path)
            if coordinates:
                request.session['coordinates'] = coordinates
            return render(request, 'sql_generate/coordinates_generator.html', {
                'processed_data': coordinates,
                'messages' : messages, 
                'feedback' : "Your file has been Uploaded",
                'form':form
                })
    else:
        form = UploadFileForm()
    return render(request, 'sql_generate/coordinates_generator.html', {'form': form})

def download_coordinates_csv(request):
    coordinates = request.session.get('coordinates', [])
    return generate_coordinates_csv_response(coordinates)
    
def map_geohashes(request):
    return render(request, 'sql_generate/Map_geohashes.html')

def map_marker(request):
    return render(request, 'sql_generate/Map_marker.html')

def polygon_query(request):
    if request.method == 'POST':
        form = PolygonForm(request.POST, request.FILES)
        if form.is_valid():
            table_name = form.cleaned_data['table_name']
            uploaded_file = request.FILES['file']
            
            # Save file content to a temporary file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(uploaded_file.read())
                temp_file_path = temp_file.name

            # Generate SQL queries
            sql_query = polygon_query_script(table_name, temp_file_path)
            
            # Remove the temporary file
            os.unlink(temp_file_path)

            # Render the response with the generated SQL queries
            return render(request, 'sql_generate/polygon_query_generator.html', {
                'sql_query': sql_query,
                'feedback': "SQL queries generated successfully.",
                'form': form
            })
        else:
            print(form.errors)
    else:
        form = PolygonForm()
    
    return render(request, 'sql_generate/polygon_query_generator.html', {'form': form})