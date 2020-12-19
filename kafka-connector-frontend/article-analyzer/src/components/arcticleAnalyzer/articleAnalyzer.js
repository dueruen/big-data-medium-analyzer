import React, {useState} from 'react';
import {publishNewArticle, testKafka} from '../../api/kafkaClient'
import './articleAnalyzer.css'

const useArticleAnalyzer = (callback) => {
    const [inputs, setInputs] = useState( { 
        title: '',
        subtitle: '',
        readingTime: '',
        publication: ''
    });

    const[articlePicture, setArticlePicture] = useState({articlePicture: ''})


    const handleSubmit = (event) => {
        if (event) {
          event.preventDefault();
        }
        callback();
      }


    const handleInputChange = (event) => {
        event.persist();

        if(event.target.files !== null) { 
            setArticlePicture(articlePicture => ({articlePicture, [event.target.name]: event.target.files[0]}));
            return;
        }
        setInputs(inputs => ({...inputs, [event.target.name]: event.target.value}));
    }
    
    return {
        handleSubmit,
        handleInputChange,
        inputs,
        articlePicture
    };
  }

const ArticleAnalyzer = () => {

    const analyzeArticle = () => {
        testKafka({
            title: inputs.title, 
            subtitle: inputs.subtitle,
            readingTime: inputs.readingTime,
            publication: inputs.publication,
            articlePicture:  articlePicture.articlePicture
        })
    }

    const {inputs, articlePicture, handleInputChange, handleSubmit} = useArticleAnalyzer(analyzeArticle);

    return(
        <div className="articleInfoFormWrapper">
            <h1>Medium Article Analyzer</h1>
            <form id="articleInfoForm" onSubmit={handleSubmit}>
                <label>
                    Title:
                    <input type="text" name="title" onChange={handleInputChange} value={inputs.title} required></input>
                </label> 
                <br/>
                <label>
                    Subtitle: 
                    <input type="text" name="subtitle" onChange={handleInputChange} value={inputs.subtitle} required></input>
                </label>
                <br/>
                <label>
                    Reading time (minutes): 
                    <input type="text" name="readingTime" onChange={handleInputChange} value={inputs.readingTime} required></input>
                </label>
                <br/>
                <label>
                    Publication: 
                    <input type="text" name="publication" onChange={handleInputChange} value={inputs.publication} required></input>
                </label>
                <br/>
                <label>
                    Article Picture: 
                    <input type="file" accept="image/*" name="articlePicture" onChange={handleInputChange} value={inputs.articlePicture} required></input>
                </label>
                <br/>
                <button type="submit">Analyze Article</button>
            </form>
        </div>
    )

}

export default ArticleAnalyzer